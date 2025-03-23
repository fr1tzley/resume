// PaymentForm.js
// This file should be placed in your static/js folder

const PaymentForm = () => {
    const [formData, setFormData] = React.useState({
      cardNumber: '',
      cardholderName: '',
      expiryDate: '',
      cvv: '',
      billingAddress: '',
      city: '',
      state: '',
      zipCode: '',
      country: 'US'
    });
    
    const [formErrors, setFormErrors] = React.useState({});
    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const [showSuccess, setShowSuccess] = React.useState(false);
  
    const handleChange = (e) => {
      const { name, value } = e.target;
      let formattedValue = value;
      
      // Format card number with spaces
      if (name === 'cardNumber') {
        formattedValue = value.replace(/\s/g, '').replace(/(\d{4})/g, '$1 ').trim().slice(0, 19);
      }
      
      // Format expiry date as MM/YY
      if (name === 'expiryDate') {
        formattedValue = value
          .replace(/\D/g, '')
          .slice(0, 4)
          .replace(/(\d{2})(\d{0,2})/, (_, p1, p2) => p2 ? `${p1}/${p2}` : p1);
      }
      
      setFormData({
        ...formData,
        [name]: formattedValue
      });
      
      // Clear error when user types
      if (formErrors[name]) {
        setFormErrors({
          ...formErrors,
          [name]: ''
        });
      }
    };
  
    const validateForm = () => {
      const errors = {};
      
      // Simple validations
      if (!formData.cardNumber.replace(/\s/g, '').match(/^\d{16}$/)) {
        errors.cardNumber = 'Please enter a valid 16-digit card number';
      }
      
      if (!formData.cardholderName) {
        errors.cardholderName = 'Cardholder name is required';
      }
      
      if (!formData.expiryDate.match(/^\d{2}\/\d{2}$/)) {
        errors.expiryDate = 'Please enter a valid expiry date (MM/YY)';
      } else {
        // Check if card is expired
        const [month, year] = formData.expiryDate.split('/');
        const expiryDate = new Date(2000 + parseInt(year), parseInt(month) - 1);
        const currentDate = new Date();
        
        if (expiryDate < currentDate) {
          errors.expiryDate = 'Card has expired';
        }
      }
      
      if (!formData.cvv.match(/^\d{3,4}$/)) {
        errors.cvv = 'CVV must be 3 or 4 digits';
      }
      
      if (!formData.billingAddress) {
        errors.billingAddress = 'Billing address is required';
      }
      
      if (!formData.city) {
        errors.city = 'City is required';
      }
      
      if (!formData.state) {
        errors.state = 'State is required';
      }
      
      if (!formData.zipCode) {
        errors.zipCode = 'ZIP code is required';
      }
      
      return errors;
    };
  
    const handleSubmit = (e) => {
      e.preventDefault();
      
      const errors = validateForm();
      setFormErrors(errors);
      
      if (Object.keys(errors).length === 0) {
        setIsSubmitting(true);
        
        // Simulate form submission
        setTimeout(() => {
          setIsSubmitting(false);
          setShowSuccess(true);
          
          // Reset form after successful submission
          setTimeout(() => {
            setShowSuccess(false);
            setFormData({
              cardNumber: '',
              cardholderName: '',
              expiryDate: '',
              cvv: '',
              billingAddress: '',
              city: '',
              state: '',
              zipCode: '',
              country: 'US'
            });
          }, 3000);
        }, 1500);
        
        // In a real-world scenario:
        // fetch('/api/update-payment', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(formData)
        // })
        // .then(response => response.json())
        // .then(data => {
        //   setIsSubmitting(false);
        //   if (data.success) {
        //     setShowSuccess(true);
        //   } else {
        //     setFormErrors({ submit: data.error });
        //   }
        // })
        // .catch(error => {
        //   setIsSubmitting(false);
        //   setFormErrors({ submit: 'Network error, please try again' });
        // });
      }
    };
  
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Payment Details</h2>
        
        {showSuccess && (
          <div className="mb-4 p-4 bg-green-100 text-green-700 rounded-md flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Payment details updated successfully!
          </div>
        )}
        
        {formErrors.submit && (
          <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-md">
            {formErrors.submit}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Card Information */}
            <div className="md:col-span-2">
              <label htmlFor="cardNumber" className="block text-sm font-medium text-gray-700 mb-1">
                Card Number
              </label>
              <input
                type="text"
                id="cardNumber"
                name="cardNumber"
                placeholder="1234 5678 9012 3456"
                value={formData.cardNumber}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${formErrors.cardNumber ? 'border-red-500' : 'border-gray-300'}`}
              />
              {formErrors.cardNumber && (
                <p className="mt-1 text-sm text-red-500">{formErrors.cardNumber}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="cardholderName" className="block text-sm font-medium text-gray-700 mb-1">
                Cardholder Name
              </label>
              <input
                type="text"
                id="cardholderName"
                name="cardholderName"
                placeholder="John Doe"
                value={formData.cardholderName}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${formErrors.cardholderName ? 'border-red-500' : 'border-gray-300'}`}
              />
              {formErrors.cardholderName && (
                <p className="mt-1 text-sm text-red-500">{formErrors.cardholderName}</p>
              )}
            </div>
            
            <div className="flex gap-4">
              <div className="flex-1">
                <label htmlFor="expiryDate" className="block text-sm font-medium text-gray-700 mb-1">
                  Expiry Date
                </label>
                <input
                  type="text"
                  id="expiryDate"
                  name="expiryDate"
                  placeholder="MM/YY"
                  value={formData.expiryDate}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md ${formErrors.expiryDate ? 'border-red-500' : 'border-gray-300'}`}
                />
                {formErrors.expiryDate && (
                  <p className="mt-1 text-sm text-red-500">{formErrors.expiryDate}</p>
                )}
              </div>
              
              <div className="w-24">
                <label htmlFor="cvv" className="block text-sm font-medium text-gray-700 mb-1">
                  CVV
                </label>
                <input
                  type="text"
                  id="cvv"
                  name="cvv"
                  placeholder="123"
                  value={formData.cvv}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md ${formErrors.cvv ? 'border-red-500' : 'border-gray-300'}`}
                />
                {formErrors.cvv && (
                  <p className="mt-1 text-sm text-red-500">{formErrors.cvv}</p>
                )}
              </div>
            </div>
            
            {/* Billing Address */}
            <div className="md:col-span-2 mt-4">
              <h3 className="font-medium text-gray-700 mb-2">Billing Address</h3>
            </div>
            
            <div className="md:col-span-2">
              <label htmlFor="billingAddress" className="block text-sm font-medium text-gray-700 mb-1">
                Street Address
              </label>
              <input
                type="text"
                id="billingAddress"
                name="billingAddress"
                placeholder="123 Main St, Apt 4B"
                value={formData.billingAddress}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${formErrors.billingAddress ? 'border-red-500' : 'border-gray-300'}`}
              />
              {formErrors.billingAddress && (
                <p className="mt-1 text-sm text-red-500">{formErrors.billingAddress}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                id="city"
                name="city"
                placeholder="New York"
                value={formData.city}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${formErrors.city ? 'border-red-500' : 'border-gray-300'}`}
              />
              {formErrors.city && (
                <p className="mt-1 text-sm text-red-500">{formErrors.city}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="state" className="block text-sm font-medium text-gray-700 mb-1">
                State
              </label>
              <input
                type="text"
                id="state"
                name="state"
                placeholder="NY"
                value={formData.state}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${formErrors.state ? 'border-red-500' : 'border-gray-300'}`}
              />
              {formErrors.state && (
                <p className="mt-1 text-sm text-red-500">{formErrors.state}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="zipCode" className="block text-sm font-medium text-gray-700 mb-1">
                ZIP Code
              </label>
              <input
                type="text"
                id="zipCode"
                name="zipCode"
                placeholder="10001"
                value={formData.zipCode}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md ${formErrors.zipCode ? 'border-red-500' : 'border-gray-300'}`}
              />
              {formErrors.zipCode && (
                <p className="mt-1 text-sm text-red-500">{formErrors.zipCode}</p>
              )}
            </div>
            
            <div>
              <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <select
                id="country"
                name="country"
                value={formData.country}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="US">United States</option>
                <option value="CA">Canada</option>
                <option value="GB">United Kingdom</option>
                <option value="AU">Australia</option>
                <option value="DE">Germany</option>
                <option value="FR">France</option>
                <option value="JP">Japan</option>
              </select>
            </div>
          </div>
          
          <div className="mt-6">
            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full py-2 px-4 rounded-md font-medium text-white ${isSubmitting ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'}`}
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : 'Update Payment Information'}
            </button>
          </div>
        </form>
      </div>
    );
  };
  
  // Make sure to register this as a global component
  window.PaymentForm = PaymentForm;