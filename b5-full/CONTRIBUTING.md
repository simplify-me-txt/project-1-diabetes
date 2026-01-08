# Contributing to Diabetes Prediction App

Thank you for considering contributing to this project! 🎉

## 🤝 How to Contribute

### 1. **Report Bugs**
- Check existing issues first
- Use the bug report template
- Include steps to reproduce
- Provide error messages/screenshots

### 2. **Suggest Features**
- Open an issue with "Feature Request" label
- Describe the use case
- Explain expected behavior

### 3. **Submit Code**

#### **Setup Development Environment**
```bash
git clone https://github.com/your-username/Diabetesprediction.git
cd Diabetesprediction
./setup.sh
```

#### **Create a Branch**
```bash
git checkout -b feature/your-feature-name
```

#### **Make Changes**
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed

#### **Test Your Changes**
```bash
# Run the app
python3 app.py

# Test manually
# - Register new user
# - Make predictions
# - Check all features work
```

#### **Commit**
```bash
git add .
git commit -m "Add: Description of your changes"
```

#### **Push and Create PR**
```bash
git push origin feature/your-feature-name
```
Then create a Pull Request on GitHub.

## 📝 Code Style

- Use **4 spaces** for indentation
- Follow **PEP 8** for Python code
- Use **descriptive variable names**
- Add **docstrings** to functions
- Keep lines **under 100 characters**

## 🧪 Testing Checklist

Before submitting a PR, ensure:
- [ ] App starts without errors
- [ ] Registration works (patient & doctor)
- [ ] Login/logout functions
- [ ] Predictions can be made
- [ ] History shows correctly
- [ ] Doctor dashboard loads
- [ ] Admin panel accessible
- [ ] No console errors

## 📋 Areas for Contribution

### **High Priority**
- [ ] Add unit tests (pytest)
- [ ] Implement session timeout
- [ ] Add rate limiting
- [ ] Multi-model ensemble
- [ ] Mobile responsiveness

### **Medium Priority**
- [ ] API development
- [ ] Advanced analytics
- [ ] Email notification system
- [ ] Multi-language support
- [ ] Dark mode

### **Documentation**
- [ ] Video tutorials
- [ ] API documentation
- [ ] Deployment guides
- [ ] User manual (PDF)

## 🙏 Thank You!

Every contribution helps make this project better!
