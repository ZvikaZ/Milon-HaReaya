import { SearchInput } from "./searchInput.tsx";

export function Navbar({
  searchKey,
  setSearchKey,
  searchAlsoContent,
  setSearchAlsoContent,
}) {
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
}
