import { Anchor, Blockquote, Popover } from "@mantine/core";
import { ContentText } from "../content/content-text.tsx";

export const Footnote: React.FC<FootnoteValueType> = ({
  number_relative,
  content,
  highlight,
}) => {
  const shouleBeOpened = highlight
    ? content.some((item) => item.text.includes(highlight))
    : false;

  const footnoteContent = content ? (
    content.map((item, index) => (
      <ContentText
        key={index}
        className={item.style}
        value={item.text}
        highlight={highlight}
      />
    ))
  ) : (
    <span></span>
  );

  return shouleBeOpened ? (
    <Blockquote>{footnoteContent}</Blockquote>
  ) : (
    <Popover
      shadow={"md"}
      width={"75%"}
      position={"bottom-start"}
      defaultOpened={shouleBeOpened}
    >
      <Popover.Target>
        <Anchor>
          <sup>({number_relative})</sup>
        </Anchor>
      </Popover.Target>
      <Popover.Dropdown
        style={{
          borderWidth: "2px",
          borderStyle: "solid",
          borderColor: "#000",
          backgroundColor: "#E8E8E8f5",
          borderRadius: "15px",
          padding: "10px",
        }}
      >
        {footnoteContent}
      </Popover.Dropdown>
    </Popover>
  );
};
