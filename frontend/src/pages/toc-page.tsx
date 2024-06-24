import React from "react";
import { useParams } from "react-router-dom";

const TocPage: React.FC = () => {
  const { tocItemKey } = useParams<{ tocItemKey: string }>();

  return (
    <div>
      <h1>Toc Item: {tocItemKey}</h1>
      {/* Render content for the specific ToC item here */}
    </div>
  );
};

export default TocPage;
