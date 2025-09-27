import React, { useEffect } from "react";

// Integrates Crisp chat. Requires REACT_APP_CRISP_WEBSITE_ID
const LiveChat = () => {
  useEffect(() => {
    const id = process.env.REACT_APP_CRISP_WEBSITE_ID;
    if (!id) return;
    window.$crisp = window.$crisp || [];
    window.CRISP_WEBSITE_ID = id;
    const d = document;
    if (!d.getElementById('crisp-chat')) {
      const s = d.createElement("script");
      s.id = 'crisp-chat';
      s.src = "https://client.crisp.chat/l.js";
      s.async = true;
      d.getElementsByTagName("head")[0].appendChild(s);
    }
  }, []);
  return null;
};

export default LiveChat;

