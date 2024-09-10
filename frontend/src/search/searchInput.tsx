import { rem, TextInput, Checkbox } from "@mantine/core";
import { IconSearch } from "@tabler/icons-react";
import { useLocation, useNavigate } from "react-router-dom";

export const SearchInput = () => {
  const navigate = useNavigate();

  const location = useLocation();
  const [, searchPathBase, encodedSearchTerm] = location.pathname.split("/");
  const searchTerm = decodeURIComponent(encodedSearchTerm || "");
  let searchAlsoContent = searchPathBase === "search_all";

  const getSearchPathBase = () =>
    `search_${searchAlsoContent ? "all" : "titles"}`;

  return (
    <>
      <TextInput
        value={searchTerm}
        placeholder={
          searchAlsoContent
            ? "חיפוש בשמות הערכים ובתוכנם"
            : "חיפוש רק בשמות הערכים"
        }
        onChange={(e) => {
          navigate(`/${getSearchPathBase()}/${e.target.value.trim()}`);
        }}
        size="xs"
        leftSection={
          <IconSearch
            style={{ width: rem(12), height: rem(12) }}
            stroke={1.5}
          />
        }
        rightSectionWidth={70}
        // rightSection={<Code className={classes.searchCode}>Ctrl + K</Code>}
        styles={{ section: { pointerEvents: "none" } }}
        mb="sm"
      />
      <Checkbox //TODO maybe modify to some other Mantine input
        label={"חיפוש גם בתוכן הערכים"}
        checked={searchAlsoContent}
        onChange={() => {
          searchAlsoContent = !searchAlsoContent;
          navigate(`/${getSearchPathBase()}/${searchTerm}`);
        }}
      />
    </>
  );
};
