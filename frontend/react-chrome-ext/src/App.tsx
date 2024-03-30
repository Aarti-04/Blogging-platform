import React, { useEffect, useState } from "react";
import "./App.css";
function App() {
  const [data, setData] = useState([]);
  useEffect(() => {
    (async () => {
      const d = await fetch("https://jsonplaceholder.typicode.com/posts");
      const d1 = await d.json();
      setData(d1);
    })();
  }, []);
  // console.log(data);

  return (
    <>
      <div className="App">Hello World this is chrome extension</div>
      {data.map((item) => {
        return (
          <>
            <h1>{item["title"]}</h1>
            <p>{item["body"]}</p>
          </>
        );
      })}
    </>
  );
}

export default App;
