import { Anchor, Popover } from "@mantine/core";

export const Footnote: React.FC<FootnoteValueType> = ({
  number_relative,
  content,
  highlight,
}) => {
  console.log("TODO: implement highlight in footnote", highlight);
  return (
    <Popover shadow={"md"} width={"75%"} position={"bottom-start"}>
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
        {content.map((item, index) => (
          <span key={index} className={item.style}>
            {item.text}
          </span>
        ))}
      </Popover.Dropdown>
    </Popover>
  );
};
