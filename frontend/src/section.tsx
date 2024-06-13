//TODO show sources tooltip on hover

import "./css/style.css";
import { ContentItem } from "./content-item.tsx";

export const Section: React.FC<{ content: string[][] }> = ({ content }) => {
  return content.map(([type, value], index) => (
    <ContentItem key={index} type={type} value={value} />
  ));
};
