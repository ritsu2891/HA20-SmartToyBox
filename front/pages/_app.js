import "../styles/globals.css";

function MyApp({ Component, pageProps }) {
  initializeLiff();
  return <Component {...pageProps} />;
}

function initializeLiff() {
  if (typeof window !== "undefined") {
    const liff = require("@line/liff");
    liff
      .init({
        liffId: process.env.LIFF_ID,
      })
      .then(() => {
        if (!liff.isLoggedIn()) {
          liff.login();
        } else {
          console.log("logged in");
          const idToken = liff.getDecodedIDToken();
          console.log(idToken);
        }
      })
      .catch((err) => {});
  }
}

export default MyApp;
