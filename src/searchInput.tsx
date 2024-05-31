import { rem, TextInput, Checkbox } from "@mantine/core";
import { IconSearch } from "@tabler/icons-react";
import { useState } from "react";

export const SearchInput = ({
  searchKey,
  setSearchKey,
  searchAlsoContent,
  setSearchAlsoContent,
}) => {
  return (
    <>
      <TextInput
        placeholder={
          searchAlsoContent
            ? "חיפוש בשמות הערכים ובתוכנם"
            : "חיפוש רק בשמות הערכים"
        }
        value={searchKey}
        onChange={(e) => setSearchKey(e.target.value)}
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
