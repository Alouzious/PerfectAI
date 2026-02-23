const Tabs = ({ tabs, activeTab, onChange }) => {
  return (
    <div className="border-b border-white/10 mb-6">
      <div className="flex gap-1 overflow-x-auto hide-scrollbar">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`px-4 sm:px-6 py-3 font-semibold text-sm sm:text-base whitespace-nowrap transition-all ${
              activeTab === tab.id
                ? 'text-white border-b-2 border-purple-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <div className="flex items-center gap-2">
              {tab.icon}
              {tab.label}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default Tabs;