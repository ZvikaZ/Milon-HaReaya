import { SearchInput } from "./searchInput.tsx";

export const Navbar: React.FC<{
  searchKey: string;
  setSearchKey: (value: string) => void;
  searchAlsoContent: boolean;
  setSearchAlsoContent: (value: boolean) => void;
}> = ({ searchKey, setSearchKey, searchAlsoContent, setSearchAlsoContent }) => {
  return (
    <>
      <SearchInput
        searchKey={searchKey}
        setSearchKey={setSearchKey}
        searchAlsoContent={searchAlsoContent}
        setSearchAlsoContent={setSearchAlsoContent}
      />
      <br />
      <div>ראשון</div>
      <div>שני</div>
    </>
  );
};
