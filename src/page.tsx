import { useQuery } from "@tanstack/react-query";

import { fetchData } from "./api.ts";

export const Page: React.FC<{ pageKey: string }> = ({ pageKey }) => {
  console.log("page", pageKey);
  const { data, error, isLoading } = useQuery({
    queryKey: ["Page", pageKey],
    queryFn: () => fetchData("page", { key: pageKey }),
  });

  if (isLoading) {
    return <div>טוען...</div>;
  }

  if (error) {
    return <div>שגיאה: {error.message}</div>;
  }

  return <pre>{JSON.stringify(data, null, 2)}</pre>;
};
