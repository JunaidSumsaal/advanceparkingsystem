import Navigation from './navigation';
import HeroSection from './hero';
import Features from './features';
import Testimonials from './testimonials';
import Footer from './footer';
import Info from './info';
import Statistics from './statistics';

export default function LandingPage () {
  return (
    <>
      <div>
        <Navigation />
        <HeroSection />
        <Features />
        <Statistics />
        <Testimonials />
        <Info />
        <Footer />
      </div>
    </>
  );
};
