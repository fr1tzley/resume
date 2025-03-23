// UsageGraph.js
// This file should be placed in your static/js folder

const UsageGraph = () => {
    const [usageData, setUsageData] = React.useState([]);
    const [selectedMonths, setSelectedMonths] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);
  
    // Sample data - replace this with your actual API call
    React.useEffect(() => {
      // Simulating API fetch
      setTimeout(() => {
        const mockData = [
          { month: 'Jan', usage: 65 },
          { month: 'Feb', usage: 59 },
          { month: 'Mar', usage: 80 },
          { month: 'Apr', usage: 81 },
          { month: 'May', usage: 56 },
          { month: 'Jun', usage: 55 },
          { month: 'Jul', usage: 40 },
          { month: 'Aug', usage: 70 },
          { month: 'Sep', usage: 90 },
          { month: 'Oct', usage: 75 },
          { month: 'Nov', usage: 62 },
          { month: 'Dec', usage: 85 }
        ];
        
        setUsageData(mockData);
        // Initially select all months
        setSelectedMonths(mockData.map(item => item.month));
        setLoading(false);
      }, 1000);
  
      // In a real-world scenario, replace with:
      // fetch('/api/usage-data')
      //   .then(response => response.json())
      //   .then(data => {
      //     setUsageData(data);
      //     setSelectedMonths(data.map(item => item.month));
      //     setLoading(false);
      //   })
      //   .catch(err => {
      //     setError('Failed to load usage data');
      //     setLoading(false);
      //   });
    }, []);
  
    const toggleMonth = (month) => {
      if (selectedMonths.includes(month)) {
        // Remove month if already selected
        setSelectedMonths(selectedMonths.filter(m => m !== month));
      } else {
        // Add month if not selected
        setSelectedMonths([...selectedMonths, month]);
      }
    };
  
    const selectAllMonths = () => {
      setSelectedMonths(usageData.map(item => item.month));
    };
  
    const clearMonthSelection = () => {
      setSelectedMonths([]);
    };
  
    // Filter data based on selected months
    const filteredData = usageData.filter(item => selectedMonths.includes(item.month));
  
    if (loading) {
      return <div className="p-4 text-center">Loading usage data...</div>;
    }
  
    if (error) {
      return <div className="p-4 text-center text-red-500">{error}</div>;
    }
  
    // Simplified usage graph when Recharts isn't available
    const renderTableView = () => {
      return (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Month</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usage</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredData.map((item) => (
                <tr key={item.month}>
                  <td className="px-6 py-4 whitespace-nowrap">{item.month}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="h-4 bg-blue-500" style={{ width: `${item.usage}px`, maxWidth: '200px' }}></div>
                      <span className="ml-2">{item.usage}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    };
  
    return (
      <div className="p-4 bg-white rounded-lg shadow-md mb-6">
        <h2 className="text-xl font-semibold mb-4">Usage Statistics</h2>
        
        {/* Month selector */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-1 mb-2">
            {usageData.map(item => (
              <button
                key={item.month}
                onClick={() => toggleMonth(item.month)}
                className={`px-3 py-1 text-sm rounded-full ${
                  selectedMonths.includes(item.month)
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                {item.month}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <button 
              onClick={selectAllMonths}
              className="px-3 py-1 text-sm bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Select All
            </button>
            <button 
              onClick={clearMonthSelection}
              className="px-3 py-1 text-sm bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Clear All
            </button>
          </div>
        </div>
        
        {/* Graph/Table */}
        <div className="w-full">
          {filteredData.length > 0 ? (
            renderTableView()
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500 py-8">
              No months selected. Please select at least one month to view data.
            </div>
          )}
        </div>
      </div>
    );
  };
  
  // Make sure to register this as a global component
  window.UsageGraph = UsageGraph;