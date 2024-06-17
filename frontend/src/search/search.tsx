import { useQuery } from "@tanstack/react-query";

import { fetchData } from "../utils/api.ts";
import { Section } from "../section.tsx";

//TODO investiage why אב returns false results (such as אמיתיות מקובלות)
//TODO allow search only in titles
//TODO make search results linkable
//TODO show where the search result is from
//TODO break large sections to smaller (such as אדם) (maybe not?)
//TODO different weights for title, content, and footnotes
//TODO NLP
//TODO retrieve footnotes and highlight them

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
    <p>
      <i>התאמה: {Math.round(result.score * 10)}</i>
      <Section
        key={result.key}
        content={result.content}
        highlight={searchKey}
      />
      <hr />
    </p>
  );
};

export const Search: React.FC<{ searchKey: string }> = ({ searchKey }) => {
  console.log("search", searchKey);
  const { data, error, isLoading } = useQuery<SearchQueryType[]>({
    queryKey: ["search", searchKey],
    queryFn: () => fetchData("search", { key: searchKey ? searchKey : " " }),
  });

  if (isLoading) {
    return <div>טוען...</div>;
  }

  if (error) {
    return <div>שגיאה: {error.message}</div>;
  }

  console.log(data);
  return (
    <>
      {data &&
        data.map((result) => (
          <SearchResult result={result} searchKey={searchKey} />
        ))}
    </>
  );
};
