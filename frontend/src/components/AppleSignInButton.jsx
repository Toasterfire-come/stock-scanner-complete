import React from "react";

const AppleSignInButton = () => {
  const url = `${process.env.REACT_APP_BACKEND_URL || ''}/auth/apple/login`;
  return (
    <a
      href={url}
      rel="noopener noreferrer"
      className="w-full h-11 sm:h-12 inline-flex items-center justify-center rounded-md border bg-black text-white hover:opacity-90 transition"
    >
      <span className="text-lg mr-2"></span>
      <span>Sign in with Apple</span>
    </a>
  );
};

export default AppleSignInButton;

