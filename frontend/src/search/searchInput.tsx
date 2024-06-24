import { rem, TextInput, Checkbox } from "@mantine/core";
import { IconSearch } from "@tabler/icons-react";
import React from "react";
import { useNavigate } from "react-router-dom";

export const SearchInput: React.FC<{
  searchKey: string;
  setSearchKey: (value: string) => void;
  searchAlsoContent: boolean;
  setSearchAlsoContent: (value: boolean) => void;
}> = ({ searchKey, setSearchKey, searchAlsoContent, setSearchAlsoContent }) => {
  const navigate = useNavigate();

  return (
    <>
      <TextInput
        placeholder={
          searchAlsoContent
            ? "חיפוש בשמות הערכים ובתוכנם"
            : "חיפוש רק בשמות הערכים"
        }
        value={searchKey}
        onChange={(e) => {
          const query = e.target.value.trim();
          setSearchKey(query);
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
      <Checkbox
        label={"חיפוש בתוכן הערכים"}
        checked={searchAlsoContent}
        onChange={() => setSearchAlsoContent(!searchAlsoContent)}
      />
    </>
  );
};
