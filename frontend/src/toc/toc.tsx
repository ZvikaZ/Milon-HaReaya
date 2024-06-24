import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { fetchData } from "../utils/api.ts";
import { TocItem } from "./tocItem.tsx";

interface TocItemType {
  key: string;
  title: string;
  appear_in_toc: boolean;
}

interface TocQueryType {
  key: string;
  data: TocItemType[];
}

export const Toc: React.FC<{ tocSectionKey: string }> = ({ tocSectionKey }) => {
  const { data, error, isLoading } = useQuery<TocQueryType>({
    queryKey: ["Toc"],
    queryFn: () => fetchData("get_misc", { key: "toc" }),
  });

  if (isLoading) {
    return <div>טוען...</div>;
  }

  if (error) {
    return <div>שגיאה: {error.message}</div>;
  }

  const toc = data?.data;

  const tocMap = toc
    ? new Map(toc.map((item) => [item.key, item.title]))
    : new Map();

  return (
    <>
      {toc &&
        toc.map((it) => (
          <Link key={it.key} to={`/toc/${it.key}`}>
            <TocItem
              linkKey={it.key}
              title={it.title}
              appear_in_toc={it.appear_in_toc}
              tocSectionTitle={tocMap.get(tocSectionKey)}
            />
          </Link>
        ))}
    </>
  );
};
