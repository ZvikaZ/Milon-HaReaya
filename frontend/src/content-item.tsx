import { Tooltip } from "@mantine/core";
import { getSource } from "./books-acronyms.tsx";

export const ContentItem: React.FC<{ type: string; value: string }> = ({
  type,
  value,
}) => {
  const tooltipLabel = type.startsWith("source") ? getSource(value) : "";
  switch (type) {
    case "new_line":
      return value === "\n" ? <br /> : <p />;
    case "heading_title":
      return <h1 className={type}>{value}</h1>;
    case "heading_section":
      return <h2 className={type}>{value}</h2>;
    case "heading_sub-section-bigger":
    case "section_title_secondary":
      return <h3 className={type}>{value}</h3>;
    case "heading_sub-section":
      return <h4 className={type}>{value}</h4>;
    case "heading_letter":
      return <h5 className={type}>{value}</h5>;

    default:
      return (
        <Tooltip
          label={tooltipLabel}
          disabled={tooltipLabel === ""}
          events={{ hover: true, touch: true, focus: false }}
        >
          <span className={type}>{value}</span>
        </Tooltip>
      );
  }
};
