<div align="center" style="vertical-align: center;">
  <img src="https://cdn.rpaka.dev/icon/ha20-toybox.png" height="80px" />
  <h1>HA20-SmartToyBox</h1>
  <h1>スマートおもちゃ箱</h1>
  <h1>愛知県大学対抗ハッカソン<br/>「HackAichi 2020」</h1>
  <h2>CKD賞受賞</h2>
</div><br/>

![動作イメージ](https://cdn.rpaka.dev/useimage/ha20-toybox/SmartToyBox.png)

## 概要

おもちゃ箱におもちゃの出し入れを検知する超音波センサを取り付け、おもちゃをしまったことを通知する IoT システムです。本システムは同じ大学のメンバー 4 人と共に共同で開発したものです。最終プレゼンテーションにて**CKD 株式会社様**より**企業賞**を受賞しました。

## 背景

在宅ワークの広がりで子どもの面倒を見つつ業務に取り組まなければならないお父さん・お母さんの手助けをテーマとして選定しました。子どもの自律的な行動のきっかけを与えられれば親を困らせることが減るだろうと考え、おもちゃのお片付けのモチベーションを高めるためにおもちゃ箱におもちゃがしまわれれているかを検知し、親に通知したり子どもにポイントを与えるといった事をしたいという結論にいたり、そのプロットタイプとしてこの IoT システムを開発しました。

## 利用

本 IoT システムは「Hack Aichi 2020」の参加に際し試作したプロトタイプであり、一般の利用を想定して作成したものではありません。本リポジトリのコードを用いて再現することはできますが、以下「構成」にあげるデバイスを必要とします。

## 構成

![構成](https://cdn.rpaka.dev/arch/ha20-toybox.jpg)
![おもちゃ箱の判別](https://cdn.rpaka.dev/useimage/ha20-toybox/sensor.jpg)

### IoT 端末

- Raspberry Pi 3B+
- 超音波センサ（HC-SR04）

![回路図](https://cdn.rpaka.dev/useimage/ha20-toybox/circuit.jpg)

### バックエンド

- AWS Lambda (Node.js 12.x)
- Amazon Dynamo DB
- AWS API Gateway

**利用ライブラリ**

- @line/bot-sdk
- aws-sdk
- dataformat
- dotenv

### フロントエンド

デモでは LINE 通知からスムーズにおもちゃ箱の状態表示画面に移れるように、LIFF アプリとして起動するように設定しました。通常のブラウザでも動作可能です。

- Netlify

**利用ライブラリ**

- React.js
- axios

## 機能

- おもちゃ箱の出し入れを検知し、リアルタイムでおもちゃ箱におもちゃが入っているかをブラウザ・LINE から確認。
- 隣接するおもちゃ箱について、どのおもちゃ箱への出し入れなのかを区別。
- おもちゃ箱を全てしまったタイミングで LINE 通知を送信。
