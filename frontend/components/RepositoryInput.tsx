type Props = {
  value: string;
  onChange: (value: string) => void;
};

export default function RepositoryInput({
  value,
  onChange,
}: Props) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium">
        GitHub Repository
      </label>

      <input
        type="text"
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
        placeholder="https://github.com/owner/repository"
        className="w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-3 outline-none focus:border-gray-500"
      />
    </div>
  );
}