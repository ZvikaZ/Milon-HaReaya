import { AppShell, Burger } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

import { Search } from "../search/search.tsx";
import { Page } from "../page.tsx";
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
  if (!type && !id) {
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
        <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
        <span>מילון הראיה</span>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <SearchInput />
        <br />
        <Toc tocSectionKey={type === "toc" ? (id as string) : ""} />
      </AppShell.Navbar>

      <AppShell.Main>
        {type === "toc" ? (
          <Page pageKey={id as string} />
        ) : type === "search" ? (
          <Search searchKey={id as string} />
        ) : (
          <NotFound />
        )}
      </AppShell.Main>
    </AppShell>
  );
};

export { MainLayout };
