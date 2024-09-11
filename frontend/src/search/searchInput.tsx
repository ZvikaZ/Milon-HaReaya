import { rem, TextInput, Checkbox, ActionIcon } from "@mantine/core";
import { IconSearch, IconX } from "@tabler/icons-react";
import { useLocation, useNavigate } from "react-router-dom";

export const SearchInput = () => {
  const navigate = useNavigate();

  const location = useLocation();
  const [, searchPathBase, encodedSearchTerm] = location.pathname.split("/");
  const searchTerm = searchPathBase.startsWith("search")
    ? decodeURIComponent(encodedSearchTerm || "")
    : "";
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
        rightSection={
          searchTerm && (
            <ActionIcon
              size="xs"
              radius="xl"
              color="gray"
              onClick={() => navigate(`/${getSearchPathBase()}/`)}
              style={{ marginRight: rem(8) }}
            >
              <IconX size={11} />
            </ActionIcon>
          )
        }
        rightSectionWidth={40}
        styles={{ section: { pointerEvents: "auto" } }}
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
