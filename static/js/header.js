// Remove the import statement
// Define React in the global scope

const { useState, useImperativeHandle, forwardRef, useRef } = React;



const DashboardHeader = ({ initialActiveButton = 'new' }) => {
  const [activeButton, setActiveButton] = React.useState(initialActiveButton);
  
  const handleButtonClick = (buttonName) => {
    setActiveButton(buttonName);

    if (buttonName == 'previous') {
      const url = new URL('./records', window.location.href);
      window.location.href = url;
    } else if (buttonName == 'new') {
      const url = new URL('./upload', window.location.href);
      window.location.href = url;
    };
  };
  
  return (
    <header className="w-full bg-gradient-to-r from-blue-600 to-indigo-700 shadow-lg p-4 mb-6">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <div className="flex space-x-2">
            <button 
              onClick={() => handleButtonClick('new')}
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                activeButton === 'new' 
                  ? 'bg-white text-blue-700 shadow-md' 
                  : 'bg-blue-500 text-white hover:bg-blue-400'
              }`}
            >
              New Analysis
            </button>
            
            <button 
              onClick={() => handleButtonClick('previous')}
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                activeButton === 'previous' 
                  ? 'bg-white text-blue-700 shadow-md' 
                  : 'bg-blue-500 text-white hover:bg-blue-400'
              }`}
            >
              Previous Analyses
            </button>
          </div>
        </div>
        
        <div className="flex items-center">
          <button className="flex items-center space-x-2 bg-blue-500 hover:bg-blue-400 text-white px-4 py-2 rounded-lg transition-all duration-200">
            <span className="font-medium">Account</span>
          </button>
        </div>
      </div>
    </header>
  );
};

// Don't export - make it available globally
 window.DashboardHeader = DashboardHeader;