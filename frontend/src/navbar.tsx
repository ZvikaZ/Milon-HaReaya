import { SearchInput } from "./search/searchInput.tsx";
import { Toc } from "./toc/toc.tsx";

export const Navbar: React.FC<{
  searchKey: string;
  setSearchKey: (value: string) => void;
  searchAlsoContent: boolean;
  setSearchAlsoContent: (value: boolean) => void;
  setTocItem: (value: string) => void;
}> = ({
  searchKey,
  setSearchKey,
  searchAlsoContent,
  setSearchAlsoContent,
  setTocItem,
}) => {
  return (
    <>
      <SearchInput
        searchKey={searchKey}
        setSearchKey={setSearchKey}
        searchAlsoContent={searchAlsoContent}
        setSearchAlsoContent={setSearchAlsoContent}
      />
      <br />
      <Toc setTocItem={setTocItem} />
    </>
  );
};
