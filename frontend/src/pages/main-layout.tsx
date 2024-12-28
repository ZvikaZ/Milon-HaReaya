import { AppShell, Burger, Group } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

import { Search } from "../search/search.tsx";
import { ContentPage } from "./content-page.tsx";
import { useParams } from "react-router-dom";
import { NotFound } from "./not-found.tsx";
import { SearchInput } from "../search/searchInput.tsx";
import { Toc } from "../toc/toc.tsx";

const defaultPage = "ערכים כלליים__page_1"; //TODO other default page?

const MainLayout = () => {
  const [opened, { toggle }] = useDisclosure();

  let { type, id } = useParams<{
    type: string;
    id: string;
  }>();
  if (!id) {
    type = "toc";
    id = defaultPage;
  }
  //TODO: maybe use Mantine's: Breadcrumbs , Anchor, Skeleton (w/ React Query)
  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: "sm",
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group align="stretch">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          {/*<span>מילון הראיה</span>*/}
          <SearchInput />
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Toc tocSectionKey={type === "toc" ? (id as string) : ""} />
      </AppShell.Navbar>

      <AppShell.Main>
        {type === "toc" || type === "section" ? (
          <ContentPage type={type} id={id as string} />
        ) : type?.startsWith("search") ? (
          <Search
            searchKey={id as string}
            searchAlsoContent={type === "search_all"}
          />
        ) : (
          <NotFound />
        )}
      </AppShell.Main>
    </AppShell>
  );
};

export { MainLayout };
