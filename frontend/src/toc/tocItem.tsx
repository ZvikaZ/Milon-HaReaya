import { Button } from "@mantine/core";

export const TocItem: React.FC<{
  title: string;
  linkKey: string;
  appear_in_toc: boolean;
  setTocItem: (value: string) => void;
  tocSection: string;
  setTocSection: (value: string) => void;
}> = ({
  title,
  linkKey,
  appear_in_toc,
  setTocItem,
  tocSection,
  setTocSection,
}) => {
  function getSectionName() {
    return appear_in_toc ? title : title[0];
  }

  if (!appear_in_toc && tocSection !== getSectionName()) return <></>;

  return (
    <Button
      variant="subtle"
      onClick={() => {
        setTocItem(linkKey);
        setTocSection(getSectionName());
      }}
    >
      {appear_in_toc ? title : title[1]}
    </Button>
  );
};
