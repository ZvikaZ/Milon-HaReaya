import { useQuery } from "@tanstack/react-query";

import { fetchData } from "../utils/api.ts";
import { Section } from "../section.tsx";
import { useEffect, useState } from "react";
import { Skeleton } from "@mantine/core";
import { useScrollIntoView } from "@mantine/hooks";

interface SectionType {
  key: string;
  title: string;
  content: string[][];
}

interface PageDataType {
  sections: SectionType[];
}

export const ContentPage: React.FC<{ id: string; type: string }> = ({
  id,
  type,
}) => {
  console.log("ContentPage", type, id);
  const [isScrolled, setIsScrolled] = useState(true);
  const { scrollIntoView, targetRef } = useScrollIntoView<HTMLDivElement>();

  const { data, error, isLoading } = useQuery<PageDataType>({
    queryKey: ["ContentPage", id],
    queryFn: () => fetchData(type === "toc" ? "page" : type, { key: id }),
  });

  useEffect(() => {
    if (data && data.sections.length > 0 && type === "section") {
      scrollIntoView({ alignment: "center" });
      setIsScrolled(true);
      const timer = setTimeout(() => {
        setIsScrolled(false);
      }, 20);

      return () => clearTimeout(timer);
    }
  }, [data, type, id, scrollIntoView]);

  if (isLoading) {
    return <div>טוען...</div>;
  }

  if (error) {
    return <div>שגיאה: {error.message}</div>;
  }

  console.log(data);
  //TODO: I dont like this skeleton, I prefer to use transition, but they start too late and that's looks bad.
  // they also pop from nowhere, I'd like to keep a placeholder for them before they appear. skeleton does this well...
  return (
    <>
      {data &&
        data.sections.map((it) => {
          return it.key === id ? (
            <Skeleton key={it.key} visible={isScrolled}>
              <div ref={targetRef}>
                <Section content={it.content} highlight={""} />
              </div>
            </Skeleton>
          ) : (
            <div key={it.key}>
              <Section content={it.content} highlight={""} />
            </div>
          );
        })}
    </>
  );
};
