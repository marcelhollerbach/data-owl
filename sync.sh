cd ./angular-site/ || exit
npx ng build --build-optimizer --base-href=/ui/ --configuration production
cd ..
rm -r ./static/ || true
rm -r ./templates/ || true
mkdir ./static/
mkdir ./templates/
cp -r ./angular-site/dist/data-manager/* ./static
mv ./static/index.html ./templates/index.html