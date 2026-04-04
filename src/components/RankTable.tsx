interface Column<T> {
  header: string;
  className?: string;
  render: (item: T, index: number) => React.ReactNode;
}

interface RankTableProps<T> {
  data: T[];
  columns: Column<T>[];
}

export default function RankTable<T>({ data, columns }: RankTableProps<T>) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 dark:border-slate-700">
            {columns.map((col, i) => (
              <th
                key={i}
                className={`px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400 ${col.className ?? ""}`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, rowIdx) => (
            <tr
              key={rowIdx}
              className="border-b border-slate-100 transition-colors hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50"
            >
              {columns.map((col, colIdx) => (
                <td key={colIdx} className={`px-3 py-2.5 ${col.className ?? ""}`}>
                  {col.render(item, rowIdx)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
