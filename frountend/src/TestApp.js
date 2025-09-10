import React from "react";

const TestApp = () => {
  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>React Test App</h1>
      <p>If you can see this, React is working!</p>
      <button onClick={() => alert("Button clicked!")}>Test Button</button>
    </div>
  );
};

export default TestApp;