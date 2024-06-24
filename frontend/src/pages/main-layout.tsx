//TODO keep in git the mongo functions, for reference

import { AppShell, Burger } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

import { Navbar } from "../navbar.tsx";
import { Search } from "../search/search.tsx";
import { useState } from "react";
import { Page } from "../page.tsx";
import { useParams } from "react-router-dom";

const MainLayout = () => {
  const [opened, { toggle }] = useDisclosure();
  const [searchAlsoContent, setSearchAlsoContent] = useState(false);
  const [searchKey, setSearchKey] = useState("");
  const [tocItem, setTocItem] = useState("ערכים כלליים-א__page_1");

  const { type, id } = useParams<{
    type: string;
    id: string;
  }>();
  console.log(`type: ${type}, id: ${id}`); //TODO use these
  // TODO get rid of some state here... (and in other places)
  //TODO clean console from many printings

  //TODO: maybe us Mantine's: Breadcrumbs , Anchor, Skeleton (w/ React Query)
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
        <Navbar
          searchKey={searchKey}
          setSearchKey={setSearchKey}
          searchAlsoContent={searchAlsoContent}
          setSearchAlsoContent={setSearchAlsoContent}
          setTocItem={setTocItem}
        />
      </AppShell.Navbar>

      <AppShell.Main>
        {!searchKey ? (
          <Page pageKey={tocItem} />
        ) : (
          <Search searchKey={searchKey} />
        )}
      </AppShell.Main>
    </AppShell>
  );
};

export { MainLayout };
