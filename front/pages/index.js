import Head from "next/head";
import styles from "../styles/Home.module.css";
import { useState, useEffect } from "react";
import axios from "axios";

function ToyBox(props) {
  return (
    <div className={styles.toyBox}>
      {/* <span>{props.status}</span> */}
      {props.status == "fill" ? <img src="toy.png" /> : <></>}
    </div>
  );
}

const config = {
  nBounds: 3,
};

const API_ENDPOINT = process.env.API_ENDPOINT;
const apiClient = axios.create({
  baseURL: API_ENDPOINT,
});

let fetcher = null;

export default function Home() {
  let [toyBoxStatus, setToyBoxStatus] = useState(["empty", "empty", "empty"]);

  let toyBoxElem = [];
  for (let i = 0; i < config.nBounds; i++) {
    toyBoxElem.push(<ToyBox key={`Toy${i}`} status={toyBoxStatus[i]}></ToyBox>);
  }

  if (typeof window !== "undefined") {
    if (!fetcher) {
      fetcher = window.setInterval(() => {
        apiClient.get("/status").then((res) => {
          const data = JSON.parse(res.data);
          const status = data.boxStatus;
          setToyBoxStatus(status);
        });
      }, 3000);
    }
  }

  return (
    <div className={styles.container}>
      <Head>
        <title>スマートおもちゃ箱</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>スマートおもちゃ箱</h1>
        <div className={styles.toyBoxRow}>{toyBoxElem}</div>
      </main>

      <footer className={styles.footer}>
        <a
          href="https://vercel.com?utm_source=create-next-app&utm_medium=default-template&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          HackAichi2020 愛知県立大学
        </a>
      </footer>
    </div>
  );
}
