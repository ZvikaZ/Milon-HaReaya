import { rem, TextInput, Checkbox } from "@mantine/core";
import { IconSearch } from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

export const SearchInput = () => {
  const navigate = useNavigate();
  const [searchAlsoContent, setSearchAlsoContent] = useState(false); //TODO connect to 'query' link

  return (
    <>
      <TextInput
        placeholder={
          searchAlsoContent
            ? "חיפוש בשמות הערכים ובתוכנם"
            : "חיפוש רק בשמות הערכים"
        }
        onChange={(e) => {
          const query = e.target.value.trim();
          if (query) {
            navigate(`/search/${query}`);
          }
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
        label={"חיפוש בתוכן הערכים"}
        checked={searchAlsoContent}
        onChange={() => setSearchAlsoContent(!searchAlsoContent)}
      />
    </>
  );
};
