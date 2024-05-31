//TODO keep in git the mongo functions, for reference

import { AppShell, Burger } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

import { Navbar } from "./navbar.tsx";
import { Search } from "./search.tsx";

const MainLayout = () => {
  const [opened, { toggle }] = useDisclosure();

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
        <Navbar></Navbar>
      </AppShell.Navbar>

      <AppShell.Main>
        {/*<Page pageKey={"p_1"} />*/}
        <Search searchKey={"אבר"} />
      </AppShell.Main>
    </AppShell>
  );
};

export { MainLayout };
