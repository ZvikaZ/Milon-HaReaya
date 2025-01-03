import { useQuery } from "@tanstack/react-query";

import { fetchData } from "../utils/api.ts";
import { Section } from "../section.tsx";
import { Link } from "react-router-dom";

//TODO show where the search result is from
//TODO move search bar above page
//TODO break large sections to smaller (such as אדם) (maybe not?)
//TODO maybe replace the skeleton after loading section with highlighting the search result in there

//TODO searching אשה fails, maybe because of ניקוד
//TODO clicking the footnotes on search results - jumps to them - not good
//TODO fix <a> warning in console
//TODO (?) focus on search input when search page is (re)loaded
//TODO when user deletes search query, return to original page
//TODO more weight to complete word (אב should be better than אבנט)
//TODO different weights for title, content, and footnotes
//TODO NLP (or maybe using N-gram indexing is simpler and good enough)
//TODO replace deprecated MongoDB HTTPS Endpoints (by September 2025)

interface SearchQueryType {
  key: string;
  title: string;
  score: number;
  content: string[][];
}

export const SearchResult: React.FC<{
  result: SearchQueryType;
  searchKey: string;
}> = ({ result, searchKey }) => {
  //TODO returns a little bit more than needed...
  // keeping it for future reference
  //
  // console.log(
  //   result.highlights.map((it) =>
  //     it.texts.filter((text) => text.type === "hit").map((text) => text.value),
  //   ),
  // );

  return (
    <Link
      to={`/section/${result.key}`}
      style={{
        textDecoration: "none",
        color: "inherit",
        fontWeight: "normal", // Override default link font-weight
      }}
    >
      <div>
        <i>התאמה: {Math.round(result.score * 10)}</i>
        <Section
          key={result.key}
          content={result.content}
          highlight={searchKey}
        />
        <hr />
      </div>
    </Link>
  );
};

export const Search: React.FC<{
  searchKey: string;
  searchAlsoContent: boolean;
}> = ({ searchKey, searchAlsoContent }) => {
  console.log("search", searchAlsoContent, searchKey);
  const { data, error, isLoading } = useQuery<SearchQueryType[]>({
    queryKey: ["search", searchKey, searchAlsoContent],
    queryFn: () =>
      fetchData("search", {
        key: searchKey ? searchKey : " ",
        searchAlsoContent: searchAlsoContent,
      }),
  });

  if (isLoading) {
    return <div>טוען...</div>;
  }

  if (error) {
    return <div>שגיאה: {error.message}</div>;
  }

  return (
    <>
      {data &&
        data.map((result, index) => (
          <SearchResult key={index} result={result} searchKey={searchKey} />
        ))}
    </>
  );
};
