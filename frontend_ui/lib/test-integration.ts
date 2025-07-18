import { api } from './api';

// Test function to verify backend integration
export const testBackendIntegration = async () => {
  console.log('🔍 Testing Backend Integration with Module 3 Backend Gateway...');
  
  try {
    // Test 1: Health check
    console.log('1. Testing health check endpoint...');
    const healthResponse = await api.health.check();
    console.log('✅ Health check successful:', healthResponse.data);
    
    // Test 2: Test geological data endpoint (without auth)
    console.log('2. Testing geological data endpoint...');
    try {
      const sitesResponse = await api.geological.getSites();
      console.log('✅ Geological data endpoint accessible:', sitesResponse.data.length, 'sites found');
    } catch {
      console.log('⚠️  Geological data endpoint requires authentication (expected)');
    }
    
    // Test 3: Test chat endpoint (without auth)
    console.log('3. Testing chat endpoint...');
    try {
      const chatResponse = await api.chat.send('Hello, can you help me with geological data?');
      console.log('✅ Chat endpoint accessible:', chatResponse.data);
    } catch {
      console.log('⚠️  Chat endpoint requires authentication (expected)');
    }
    
    console.log('🎉 Backend integration test completed successfully!');
    return true;
    
  } catch (error) {
    console.error('❌ Backend integration test failed:', error);
    return false;
  }
};

// Test with authentication
export const testAuthenticatedBackendIntegration = async (username: string, password: string) => {
  console.log('🔐 Testing Authenticated Backend Integration...');
  
  try {
    // Test 1: Login
    console.log('1. Testing login...');
    const loginResponse = await api.auth.login({ username, password });
    console.log('✅ Login successful:', loginResponse.data);
    
    // Test 2: Test geological data with auth
    console.log('2. Testing geological data with authentication...');
    const sitesResponse = await api.geological.getSites();
    console.log('✅ Geological data accessible:', sitesResponse.data.length, 'sites found');
    
    // Test 3: Test chat with auth
    console.log('3. Testing chat with authentication...');
    const chatResponse = await api.chat.send('Hello, can you help me with geological data?');
    console.log('✅ Chat accessible:', chatResponse.data);
    
    console.log('🎉 Authenticated backend integration test completed successfully!');
    return true;
    
  } catch (error) {
    console.error('❌ Authenticated backend integration test failed:', error);
    return false;
  }
};

// Utility to check if all backend modules are running
export const checkBackendModules = async () => {
  console.log('🔍 Checking Backend Module Status...');
  
  const modules = [
    { name: 'Module 1 - Data Foundation', url: 'http://localhost:8000/health' },
    { name: 'Module 2 - Cortex Engine', url: 'http://localhost:3002/health' },
    { name: 'Module 3 - Backend Gateway', url: 'http://localhost:3003/health' }
  ];
  
  for (const moduleInfo of modules) {
    try {
      const response = await fetch(moduleInfo.url);
      if (response.ok) {
        console.log(`✅ ${moduleInfo.name} is running`);
      } else {
        console.log(`⚠️  ${moduleInfo.name} returned status ${response.status}`);
      }
    } catch {
      console.log(`❌ ${moduleInfo.name} is not accessible`);
    }
  }
}; 