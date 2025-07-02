import img1 from '../images/banner-horizontal-default-en.png';
import img2 from '../images/aila_new.png';
import img3 from '../images/up_2017_logo_en.png';

export const Template = () => {
  return (
    <div className="flex flex-col items-center p-8 bg-gray-100">
      <div className="text-2xl font-bold mb-8 text-center text-gray-800">
        AILA CHATBOT DEMO
      </div>
      <div className="flex flex-wrap justify-center gap-8">
        <img
          src={img1}
          alt="AUTH logo"
          className="max-w-full w-[440px] h-auto object-contain rounded-lg shadow-md transition-transform duration-200 ease-in-out hover:scale-105"
        />
        <img
          src={img2}
          alt="AILA project logo"
          className="max-w-full w-[440px] h-auto object-contain rounded-lg shadow-md transition-transform duration-200 ease-in-out hover:scale-105"
        />
        <img
          src={img3}
          alt="Upatras logo"
          className="max-w-full w-[440px] h-auto object-contain rounded-lg shadow-md transition-transform duration-200 ease-in-out hover:scale-105"
        />
      </div>
    </div>
  );
};
