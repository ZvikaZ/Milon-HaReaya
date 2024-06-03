import { useQuery } from "@tanstack/react-query";

import { fetchData } from "./api.ts";
import { TocItem } from "./tocItem.tsx";

interface TocItemType {
  key: string;
  title: string;
  appear_in_toc: boolean;
}

export const Toc: React.FC<{ setTocItem: (value: string) => void }> = ({
  setTocItem,
}) => {
  console.log("toc");
  const { data, error, isLoading } = useQuery<TocItemType[]>({
    queryKey: ["Toc"],
    queryFn: () => fetchData("get_misc", { key: "toc" }),
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
        data.map((it) => (
          <TocItem
            key={it.key}
            linkKey={it.key}
            title={it.title}
            appear_in_toc={it.appear_in_toc}
            setTocItem={setTocItem}
          />
        ))}
    </>
  );
};
