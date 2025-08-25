import { Tabs, TabList, TabPanels, Tab, TabPanel, Box } from "@chakra-ui/react";
import BookingList from "../../../components/parking/BookingsList";
import FacilitiesList from "../../../components/parking/FacilitiesList";
import NearbySpots from "../../../components/parking/NearbySpots";
import PricingPanel from "../../../components/parking/PricingPanel";
export default function UserDashboard() {
  return (
    <Box p={6}>
      <Tabs variant="enclosed" isFitted>
        <TabList>
          <Tab>Bookings</Tab>
          <Tab>Facilities</Tab>
          <Tab>Nearby Spots</Tab>
          <Tab>Pricing</Tab>
        </TabList>
        <TabPanels>
          <TabPanel><BookingList /></TabPanel>
          <TabPanel><FacilitiesList /></TabPanel>
          <TabPanel><NearbySpots /></TabPanel>
          <TabPanel><PricingPanel /></TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}
