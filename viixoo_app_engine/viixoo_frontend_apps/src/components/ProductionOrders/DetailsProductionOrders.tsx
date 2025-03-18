import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Text,
  VStack,
  Tabs,
  Table,
  Box,
} from "@chakra-ui/react"
import { useState } from "react"
import { GrView } from "react-icons/gr";

import type { ProductionOrderPublic } from "../../client/types.gen"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"


interface ProductionOrderProps {
  item: ProductionOrderPublic
}

export const DetailsProductionOrder = ({ item }: ProductionOrderProps) => {
  const [isOpen, setIsOpen] = useState(false) 

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button size="xs" colorPalette="gray" variant="ghost">
          <GrView fontSize="16px" />
          Detalles
        </Button>
      </DialogTrigger>
      <DialogContent maxH="90vh">
        <form>
          <DialogHeader>
            <DialogTitle>Orden de fabricación</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <VStack gap={4}>
              <Field
                label="Referencia"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.name || ""}
                </Text>
              </Field>

              <Field
                label="Producto"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.product || ""}
                </Text>
              </Field>
              <Field
                label="Cantidad"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.product_qty || ""}
                </Text>
              </Field>
              <Field
                label="Lista de materiales"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.bom || ""}
                </Text>
              </Field>
              <Field
                label="Fecha inicio"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.date_start || ""}
                </Text>
              </Field>
              <Field
                label="Fecha fin"
              >
                <Text
                  fontSize="md"
                  py={2}
                  color="inherit"
                  truncate
                  maxW="sm"
                >
                  {item?.date_start || ""}
                </Text>
              </Field>
              <Tabs.Root defaultValue="work-order" variant="subtle">
                <Tabs.List>
                    <Tabs.Trigger key="1" value="work-order">
                    Órdenes de trabajo
                    </Tabs.Trigger>
                    <Tabs.Trigger key="2" value="list-components">
                    Lista de componentes
                    </Tabs.Trigger>
                </Tabs.List>
               <Tabs.Content key="1" value="work-order">
                <Box maxH="100px" overflowY="auto" borderWidth="1px" borderRadius="md">
                    <Table.Root maxH="100px" size="sm" showColumnBorder>
                      <Table.Header>
                        <Table.Row>
                          <Table.ColumnHeader w="sm">Referencia</Table.ColumnHeader>
                          <Table.ColumnHeader w="sm">Producto</Table.ColumnHeader>
                          <Table.ColumnHeader w="sm">Cantidad a producir</Table.ColumnHeader>
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                        {item.workorder_ids?.map((workorder) => (
                          <Table.Row key={workorder.workorder_id}>
                            <Table.Cell truncate maxW="sm">
                              {workorder.name}
                            </Table.Cell>
                            <Table.Cell truncate maxW="sm">
                              {workorder.product}
                            </Table.Cell>
                            <Table.Cell truncate maxW="30%">
                              {workorder.qty_remaining}
                            </Table.Cell>
                          </Table.Row>
                        ))}
                      </Table.Body>
                    </Table.Root>
                  </Box>
                </Tabs.Content>                
                <Tabs.Content key="2" value="list-components">
                  <Box maxH="100px" overflowY="auto" borderWidth="1px" borderRadius="md">
                    <Table.Root maxH="100px" size="sm" showColumnBorder>
                      <Table.Header>
                        <Table.Row>
                          <Table.ColumnHeader w="sm">Producto</Table.ColumnHeader>
                          <Table.ColumnHeader w="sm">Cantidad</Table.ColumnHeader>
                        </Table.Row>
                      </Table.Header>
                      <Table.Body>
                        {item.move_raw_ids?.map((comp) => (
                          <Table.Row key={comp.move_raw_id}>
                            <Table.Cell truncate maxW="sm">
                              {comp.product}
                            </Table.Cell>
                            <Table.Cell truncate maxW="30%">
                              {comp.quantity}
                            </Table.Cell>
                          </Table.Row>
                        ))}
                      </Table.Body>
                    </Table.Root>
                  </Box>
                </Tabs.Content>
              </Tabs.Root>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                >
                  Cerrar
                </Button>
              </DialogActionTrigger>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}
