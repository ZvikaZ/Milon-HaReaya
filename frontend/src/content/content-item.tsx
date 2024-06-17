import { Tooltip } from "@mantine/core";
import { getSource } from "../utils/books-acronyms.tsx";
import { Footnote } from "../footnotes/footnote.tsx";
import { ContentText } from "./content-text.tsx";

export const ContentItem: React.FC<ContentType> = ({
  type,
  value,
  highlight,
}) => {
  const tooltipLabel = type.startsWith("source")
    ? getSource(value as string)
    : "";
  switch (type) {
    case "new_line":
      return value === "\n" ? <br /> : <p />;
    case "heading_title":
      return <h1 className={type}>{value as string}</h1>;
    case "heading_section":
      return <h2 className={type}>{value as string}</h2>;
    case "heading_sub-section-bigger":
    case "section_title_secondary":
      return <h3 className={type}>{value as string}</h3>;
    case "heading_sub-section":
      return <h4 className={type}>{value as string}</h4>;
    case "heading_letter":
      return <h5 className={type}>{value as string}</h5>;
    case "footnote":
    case "footnote_recurrence":
      value = value as FootnoteValueType;
      return (
        <Footnote
          number_relative={value.number_relative}
          number_abs={value.number_abs}
          content={value.content}
          highlight={highlight}
        />
      );

    default:
      return (
        <Tooltip
          label={tooltipLabel}
          disabled={tooltipLabel === ""}
          events={{ hover: true, touch: true, focus: false }}
        >
          <ContentText
            className={type}
            value={value as string}
            highlight={highlight}
          />
        </Tooltip>
      );
  }
};
