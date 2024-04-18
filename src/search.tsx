import { rem, TextInput } from "@mantine/core";
import { IconSearch } from "@tabler/icons-react";

export const Search = () => {
  return (
    <TextInput
      placeholder="חיפוש"
      size="xs"
      leftSection={
        <IconSearch style={{ width: rem(12), height: rem(12) }} stroke={1.5} />
      }
      rightSectionWidth={70}
      // rightSection={<Code className={classes.searchCode}>Ctrl + K</Code>}
      styles={{ section: { pointerEvents: "none" } }}
      mb="sm"
    />
  );
};
