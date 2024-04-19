import { AppShell, Burger } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Navbar } from "./navbar.tsx";

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
        <span>
          <span> </span>
          <span>מילון הראיה</span>
          <span> / </span>
          <span>י ניסן תשפד</span>
        </span>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Navbar></Navbar>
      </AppShell.Navbar>

      <AppShell.Main>המון דברים ממילון הראיה</AppShell.Main>
    </AppShell>
  );
};

export { MainLayout };
