import { Button } from "@mantine/core";

export const TocItem: React.FC<{
  title: string;
  linkKey: string;
  appear_in_toc: boolean;
  tocSectionTitle: string;
}> = ({ title, appear_in_toc, tocSectionTitle }) => {
  function getSectionName(value: string | string[]) {
    return Array.isArray(value) ? value[0] : value;
  }

  if (
    !appear_in_toc &&
    getSectionName(title) !== getSectionName(tocSectionTitle)
  )
    return <></>;

  return <Button variant="subtle">{appear_in_toc ? title : title[1]}</Button>;
};
