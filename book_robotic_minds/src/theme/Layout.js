import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import Chatbot from '../components/Chatbot';

export default function Layout(props) {
  return (
    <>
      <OriginalLayout {...props} />
      <Chatbot />
    </>
  );
}