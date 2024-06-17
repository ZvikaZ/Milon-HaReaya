//TODO show sources tooltip on hover

import "./css/style.css";
import { ContentItem } from "./content/content-item.tsx";

export const Section: React.FC<{ content: string[][]; highlight: string }> = ({
  content,
  highlight,
}) => {
  return content.map(([type, value], index) => (
    <ContentItem key={index} type={type} value={value} highlight={highlight} />
  ));
};
