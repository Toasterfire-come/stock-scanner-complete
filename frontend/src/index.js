import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error, info) {
    try {
      fetch('/error-beacon', { method: 'POST', keepalive: true, body: JSON.stringify({ m: error?.message?.slice(0,200), s: info?.componentStack?.slice(0,200) }) });
    } catch (e) {}
  }
  render() { return this.state.hasError ? <div className="p-6"><h1 className="text-2xl font-bold">Something went wrong</h1><p className="text-gray-600">Please refresh the page.</p></div> : this.props.children; }
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
);
