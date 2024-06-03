import { Button } from "@mantine/core";

export const TocItem: React.FC<{
  title: string;
  linkKey: string;
  appear_in_toc: boolean;
  setTocItem: (value: string) => void;
}> = ({ title, linkKey, appear_in_toc, setTocItem }) => {
  // TODO make it disappear according to appear_in_toc
  // TODO what do we want for 'ערכים כלליים'?
  return (
    <Button variant="subtle" onClick={() => setTocItem(linkKey)}>
      {appear_in_toc ? title : title[1]}
    </Button>
  );
};
