var AWS = require("aws-sdk");
require("dotenv").config();
const dateformat = require("dateformat");

AWS.config.update({
  region: "us-east-1",
});

const LIFF_URL = process.env.LIFF_URL;

var docClient = new AWS.DynamoDB.DocumentClient();

function getData() {
  return new Promise((resolve, reject) => {
    var params = {
      TableName: "SmartToyBox",
      Key: {
        key: "Status",
      },
    };
    docClient.get(params, function (err, data) {
      if (err) {
        console.error(
          "Unable to read item. Error JSON:",
          JSON.stringify(err, null, 2)
        );
        reject();
      } else {
        resolve(JSON.stringify(data.Item, null, 2));
      }
    });
  });
}

function updateStatus(newStatus) {
  return new Promise((resolve, reject) => {
    if (!Array.isArray(newStatus)) {
      resolve(false);
      return;
    }
    var params = {
      TableName: "SmartToyBox",
      Key: {
        key: "Status",
      },
      UpdateExpression: "set boxStatus = :l",
      ExpressionAttributeValues: {
        ":l": newStatus,
      },
    };
    docClient.update(params, function (err, data) {
      if (err) {
        console.error(
          "Unable to read item. Error JSON:",
          JSON.stringify(err, null, 2)
        );
        reject();
      }

      let allFill = true;
      for (let i = 0; i < newStatus.length; i++) {
        if (newStatus[i] != "fill") {
          allFill = false;
          break;
        }
      }
      if (allFill) {
        notifFillComplete();
      }

      resolve(true);
    });
  });
}
function notifFillComplete() {
  const line = require("@line/bot-sdk");

  const client = new line.Client({
    channelAccessToken: process.env.LINE_CHANNEL_ACCESS_TOKEN,
  });

  const now = new Date();

  const message = {
    type: "flex",
    altText: "お片付けできました！",
    contents: {
      type: "bubble",
      hero: {
        type: "image",
        url:
          "https://2.bp.blogspot.com/-_vJ_hbnq1_Y/UnIEMYXgTMI/AAAAAAAAZ_0/7UzK9am-7Lo/s800/omochabako.png",
        size: "full",
        aspectRatio: "20:13",
        aspectMode: "cover",
        action: {
          type: "uri",
          uri: LIFF_URL,
        },
      },
      body: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "text",
            text: "お片付けできました！",
            weight: "bold",
            size: "xl",
          },
          {
            type: "box",
            layout: "vertical",
            margin: "lg",
            spacing: "sm",
            contents: [
              {
                type: "box",
                layout: "baseline",
                spacing: "sm",
                contents: [
                  {
                    type: "text",
                    text: "時刻",
                    color: "#aaaaaa",
                    size: "sm",
                    flex: 1,
                  },
                  {
                    type: "text",
                    text: dateformat(now, "HH時MM分ss秒"),
                    wrap: true,
                    color: "#666666",
                    size: "sm",
                    flex: 5,
                  },
                ],
              },
            ],
          },
        ],
      },
      footer: {
        type: "box",
        layout: "vertical",
        spacing: "sm",
        contents: [
          {
            type: "button",
            style: "link",
            height: "sm",
            action: {
              type: "uri",
              label: "おもちゃ箱を見る",
              uri: LIFF_URL,
            },
          },
          {
            type: "spacer",
            size: "sm",
          },
        ],
        flex: 0,
      },
    },
  };

  client
    .pushMessage(process.env.LINE_DEST_USERID, message)
    .then(() => {
      console.log("success");
    })
    .catch((err) => {
      console.log(err);
    });
}

async function handler(event) {
  const method = event.httpMethod;
  const path = event.path;
  let body = event.body;
  let response = null;

  try {
    body = JSON.parse(body);
  } catch (e) {}

  try {
    if (method == "GET" && path == "/status") {
      response = await getData();
    }
    if (method == "POST" && path == "/status") {
      response = await updateStatus(body.status);
    }
  } catch (e) {
    response = "ER";
  }

  return {
    statusCode: 200,
    body: JSON.stringify(response),
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  };
}

module.exports = { handler };
