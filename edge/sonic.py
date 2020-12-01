#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO
import smbus
import requests
import json
import threading
import os
from dotenv import load_dotenv
load_dotenv()

API_ENDPOINT = os.environ['API_ENDPOINT']


class BoxState():
  state = 'empty'  # empty empty-cd fill-cd fill
  cdCount = 0

  def reset(self):
    self.state = 'empty'

  def clock(self):
    if (self.state == 'fill-cd' or self.state == 'empty-cd'):
      self.cdCount = self.cdCount + 1
    else:
      self.cdCount = 0

    if (self.cdCount > 10):
      if (self.state == 'fill-cd'):
        self.state = 'empty'
      elif (self.state == 'empty-cd'):
        self.state = 'fill'
      self.cdCount = 0

  def back_triggered(self):
    if (self.state == 'fill-cd'):
      self.state = 'fill'
      return
    if (self.state == 'fill'):
      self.state = 'empty-cd'
      return

  def front_triggered(self):
    if (self.state == 'empty-cd'):
      self.state = 'empty'
      return
    if (self.state == 'empty'):
      self.state = 'fill-cd'
      return


config = {
    "numBound": 3,
    "bound": [18, 18, 18],
    "isBox": [False, True, True]
}

boxStates = []

bus = smbus.SMBus(1)
BACK_TRIGGER = 4
BACK_ECHO = 17
FRONT_TRIGGER = 27
FRONT_ECHO = 22

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BACK_TRIGGER, GPIO.OUT)  # back Trigger
GPIO.setup(BACK_ECHO, GPIO.IN)  # back Echo
GPIO.setup(FRONT_TRIGGER, GPIO.OUT)  # front Trigger
GPIO.setup(FRONT_ECHO, GPIO.IN)  # front Echo

FRONT = 0
BACK = 1


def init():
  # 状態遷移モデルを作成
  for i in range(config["numBound"]):
    boxStates.append(BoxState())


def printBoxState():
  for i in range(config["numBound"]):
    print(boxStates[i].state, end='  ')
  print("\n")


def reading_sonic(temp):
  # 計測指示用パルス波を送信するGPIOを初期化
  GPIO.output(FRONT_TRIGGER, GPIO.LOW)
  GPIO.output(BACK_TRIGGER, GPIO.LOW)
  time.sleep(0.1)

  # 10usのパルス波を送信（計測を指示するトリガー）
  GPIO.output(FRONT_TRIGGER, True)
  GPIO.output(BACK_TRIGGER, True)
  time.sleep(0.00001)
  GPIO.output(FRONT_TRIGGER, False)
  GPIO.output(BACK_TRIGGER, False)

  # Echoに帰ってきたパルス持続時間を計測
  signaloffFront = -1
  signaloffBack = -1
  signalonFront = -1
  signalonBack = -1
  timepassedFront = -1
  timepassedBack = -1
  while timepassedFront == -1 or timepassedBack == -1:
    # Front
    if GPIO.input(FRONT_ECHO) == 0 and signalonFront == -1:
      signaloffFront = time.time()
    if GPIO.input(FRONT_ECHO) == 1:
      signalonFront = time.time()
    if GPIO.input(FRONT_ECHO) == 0 and signalonFront != -1:
      timepassedFront = signalonFront - signaloffFront
    # Back
    if GPIO.input(BACK_ECHO) == 0 and signalonBack == -1:
      signaloffBack = time.time()
    if GPIO.input(BACK_ECHO) == 1:
      signalonBack = time.time()
    if GPIO.input(BACK_ECHO) == 0 and signalonBack != -1:
      timepassedBack = signalonBack - signaloffBack

  # 距離に変換（単位：cm）
  distanceFront = timepassedFront * (331.50 + 0.606681 * temp) * 100/2
  distanceBack = timepassedBack * (331.50 + 0.606681 * temp) * 100/2

  # 返却
  return [distanceFront, distanceBack]
  GPIO.cleanup()


def detectBox(distances):
  result = []
  for distance in distances:
    cDistance = 0
    for i in range(config["numBound"]):
      bound = config["bound"][i]
      cDistance = cDistance + bound
      if (distance < cDistance):
        result.append(i)
        break
      if (i == config["numBound"] - 1):
        result.append(-1)
        break
  return result


prevBoxes = [-1, -1]
boxContinueCounts = [0, 0]
BOX_CONTINUE_TRIGGER_NUM = 3


def updateState(distances):
  currentBoxes = detectBox(distances)

  if (prevBoxes[FRONT] == currentBoxes[FRONT]):
    boxContinueCounts[FRONT] = boxContinueCounts[FRONT]+1
  else:
    boxContinueCounts[FRONT] = 0
  prevBoxes[FRONT] = currentBoxes[FRONT]

  if (prevBoxes[BACK] == currentBoxes[BACK]):
    boxContinueCounts[BACK] = boxContinueCounts[BACK]+1
  else:
    boxContinueCounts[BACK] = 0
  prevBoxes[BACK] = currentBoxes[BACK]

  if (boxContinueCounts[FRONT] > BOX_CONTINUE_TRIGGER_NUM and currentBoxes[FRONT] != -1):
    print('front trigger')
    boxStates[currentBoxes[FRONT]].front_triggered()
    boxContinueCounts[FRONT] = 0

  if (boxContinueCounts[BACK] > BOX_CONTINUE_TRIGGER_NUM and currentBoxes[BACK] != -1):
    print('back trigger')
    boxStates[currentBoxes[BACK]].back_triggered()
    boxContinueCounts[BACK] = 0


prevSentBoxStates = ['', '', '']


def sendState():
  try:
    while True:
      time.sleep(5)
      for i in range(config["numBound"]):
        if (boxStates[i].state == 'empty-cd' or boxStates[i].state == 'fill-cd'):
          print("cd found, send skip")
          continue

      changeFound = False
      for i in range(config["numBound"]):
        if (boxStates[i].state != prevSentBoxStates[i]):
          changeFound = True
          prevSentBoxStates[i] = boxStates[i].state

      if (not changeFound):
        print("change not found, send skip")
        continue

      print("status changed")

      payload = {"status": prevSentBoxStates}
      r = requests.post(API_ENDPOINT + "/status", data=json.dumps(payload))

      print(r.text)
  except KeyboardInterrupt:
    pass


try:
  init()
  apiFetchThread = threading.Thread(target=sendState)
  apiFetchThread.start()
  while True:
    [f, b] = reading_sonic(20)
    # print("front = ", round(f, 1), "[cm]")
    # print("back = ", round(b, 1), "[cm]")
    # print(detectBox([f, b]))
    updateState([f, b])
    for i in range(config["numBound"]):
      boxStates[i].clock()
    printBoxState()
    time.sleep(0.1)
except KeyboardInterrupt:
  pass
  apiFetchThread.join()

GPIO.cleanup()
