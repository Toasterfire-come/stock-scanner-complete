import React, { useEffect, useState } from "react";

export default function ThemeToggle(){
  const [isDark, setIsDark] = useState(false);

  useEffect(()=>{
    const saved = localStorage.getItem("theme");
    const prefers = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const dark = saved ? saved === 'dark' : prefers;
    setIsDark(dark);
    document.documentElement.classList.toggle('dark', dark);
  },[]);

  const toggle = () => {
    const next = !isDark;
    setIsDark(next);
    document.documentElement.classList.toggle('dark', next);
    localStorage.setItem('theme', next ? 'dark' : 'light');
  };

  return (
    <button aria-label="Toggle theme" onClick={toggle} className="btn btn-outline px-3 py-2">
      {isDark ? 'Light' : 'Dark'}
    </button>
  );
}